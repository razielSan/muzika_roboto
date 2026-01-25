import pytest

from core.module_loader.scaffolding.creator import create_module


@pytest.mark.parametrize(
    "module",
    ["test", "test.test.test", "test.test.test.test.data.test.data"],
)
def test_create_module_success(tmp_path, module):
    root_dir = tmp_path
    root_dir.mkdir(parents=True, exist_ok=True)

    module_name = module
    root_package = "test_app.bot.modules"

    response_create_module = create_module(
        module_name=module_name,
        root_package=root_package,
        root_dir=tmp_path,
    )
    assert response_create_module.data == "success"
    assert response_create_module.error is None

    module_path = (
        root_dir
        / root_package.replace(".", "/")
        / module_name.replace(".", "/childes/")
    )
    assert module_path.exists()

    # Основные файлы  должны существовать
    for filename in ["router.py", "settings.py", "response.py"]:
        assert (module_path / filename).exists()

    # Основные директории
    for dirname in [
        "childes",
        "fsm",
        "services",
        "utils",
        "handlers",
        "keyboards",
        "api",
    ]:
        assert (module_path / dirname).exists()
        assert ((module_path / dirname) / "__init__.py").exists()

    # Проверяем что переменные роутер и settings созданы в файлах
    router_file = module_path / "router.py"
    content = router_file.read_text(encoding="utf-8")
    assert "router" in content

    settings_file = module_path / "settings.py"
    content = settings_file.read_text(encoding="utf-8")
    assert "settings" in content


def test_two_create_module_success(tmp_path):
    """
    Проверяет корректно подставленных значений в первом модуле
    после создания второго

    """

    root_dir = tmp_path
    root_dir.mkdir(parents=True, exist_ok=True)
    root_package = "test_app.bot.modules"

    # создаем первый модуль
    first_module_name = "test"

    response_create_module = create_module(
        module_name=first_module_name,
        root_package=root_package,
        root_dir=tmp_path,
    )
    assert response_create_module.data == "success"
    assert response_create_module.error is None

    first_module_path = (
        root_dir
        / root_package.replace(".", "/")
        / first_module_name.replace(".", "/childes/")
    )
    assert first_module_path.exists()

    # создаем второй модуль
    second_module_name = "test.data"

    response_create_module = create_module(
        module_name=second_module_name,
        root_package=root_package,
        root_dir=tmp_path,
    )

    assert response_create_module.data == "success"
    assert response_create_module.error is None

    second_module_path = (
        root_dir
        / root_package.replace(".", "/")
        / second_module_name.replace(".", "/childes/")
    )
    assert second_module_path.exists()

    # Проверяем что во 2 модуле в settings имена подставленны корректно
    second_router_file = second_module_path / "settings.py"
    content = second_router_file.read_text(encoding="utf-8")
    assert "{" not in str(content)
    assert "}" not in str(content)

    # Проверка 1 модуля на подставление имени после создания второго, settings
    first_router_file = first_module_path / "settings.py"
    content = first_router_file.read_text(encoding="utf-8")
    assert "{" not in str(content)
    assert "}" not in str(content)
