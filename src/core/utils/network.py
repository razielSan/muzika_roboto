import base64
from pathlib import Path

from aiohttp import ClientSession

from core.response.response_data import NetworkResponseResult, LoggingData
from core.error_handlers.network import error_handler_for_the_website
from core.error_handlers.helpers import network_fail, network_ok
from core.error_handlers.format import format_errors_message
from core.response.messages import messages


async def get_and_save_image(
    data_requests: str,
    path_img: Path,
    session: ClientSession,
    logging_data: LoggingData,
    base_64: bool = False,
) -> NetworkResponseResult:
    """
    Сохраняет data_requests по указанному пути, если base_64 = True.

    Если data_requests это URL.Заходит по url, скачивает изображение
    и сохраняет его по указанному пути

    Args:
        data_requests (str): URL для скачивания или строка в кодировке base64
        path_img (Path): Путь до картинки
        session (ClientSession): Cессия для запроса
        logging_data (LoggingData): Обьект класса LoggingData содержащий в себе логгер и имя роутера
        base_64 (Optional[bool], optional): Проверка на кодировку base_64. По умолачанию None

    Returns:
        NetworkResponseResult: Объект с результатом запроса.

        атрибуты NetworkResponseResult:
            - ok (bool)
            - data (Optional, Any)
            - url (str)
            - status (int)
            - method (str)
            - headers (Optional, Dict)
            - error (Optional, Error)
            
        атрибуты Error:
            - code (str)
            - message (str)
            - details (Optional[Any])
    """
    try:
        if base_64:
            image_file: bytes = base64.b64decode(data_requests)

            path_img.parent.mkdir(parents=True, exist_ok=True)
            with open(path_img, "wb") as image:
                image.write(image_file)
        else:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            }
            # Делаем запрос на сайт для получения данных о картинке
            response = await error_handler_for_the_website(
                session=session,
                url=data_requests,
                logging_data=logging_data,
                data_type="BYTES",
                timeout=5,
                headers=headers,
                function_name=get_and_save_image.__name__,
            )
            if not response.ok:
                return response

            # Получаем расширение для картинки, если есть
            ext: bool = None
            content_type = response.headers.get("Content-Type", "")
            if "image/" in content_type:
                ext = content_type.split("/")[-1]
            if ext:
                img_name = path_img.name.split(".")[0]  # 4343sds3434321.jpg
                ext = ext.split(";")[0]
                ext = ext.split("+")[0]  # svg+lxml
                path_img = path_img.parent / f"{img_name}.{ext}"

            # Создаем папки если не существуют
            path_img.parent.mkdir(parents=True, exist_ok=True)

            with open(path_img, "wb") as file:
                file.write(response.data)

        return network_ok(
            data=path_img,
            url=response.url,
            method=response.method,
            status=response.status,
        )

    except Exception as err:
        logging_data.error_logger.exception(
            format_errors_message(
                name_router=logging_data.router_name,
                method="GET",
                status=0,
                url="base64" if base64 else data_requests,
                error_text=str(err),
                function_name=get_and_save_image.__name__,
            )
        )
        return network_fail(
            code="SERVER_ERROR",
            message=messages.SERVER_ERROR,
            method="GET",
            status=0,
            url="base64" if base64 else data_requests,
        )
