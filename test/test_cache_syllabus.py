from types import SimpleNamespace

import coursera_helper.coursera_dl as coursera_dl


class FakeExtractor:
    def __init__(self, session):
        self.session = session

    def get_modules(
        self,
        class_name,
        reverse,
        unrestricted_filenames,
        subtitle_language,
        video_resolution,
        download_quizzes,
        mathjax_cdn_url,
        download_notebooks,
    ):
        return False, []


class FakeDownloader:
    skipped_urls = []
    failed_urls = []

    def download_modules(self, modules):
        return False


def make_args(**overrides):
    values = {
        "cache_syllabus": False,
        "reverse": False,
        "unrestricted_filenames": False,
        "subtitle_language": "all",
        "video_resolution": "540p",
        "download_quizzes": False,
        "mathjax_cdn_url": "https://cdn.mathjax.org/mathjax/latest/MathJax.js",
        "download_notebooks": False,
        "only_syllabus": True,
        "cookies_file": None,
        "jobs": 1,
        "ignore_formats": None,
        "path": "",
        "disable_url_skipping": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_cache_syllabus_boolean_is_not_called(monkeypatch):
    monkeypatch.setattr(coursera_dl, "CourseraExtractor", FakeExtractor)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("spit_json should not be called")

    monkeypatch.setattr(coursera_dl, "spit_json", fail_if_called)
    monkeypatch.setattr(coursera_dl, "is_debug_run", lambda: False)

    args = make_args(cache_syllabus=False)

    error_occurred, completed = coursera_dl.download_on_demand_class(
        session=object(),
        args=args,
        class_name="fake-course",
    )

    assert error_occurred is False
    assert completed is False


def test_cache_syllabus_writes_when_enabled(monkeypatch):
    monkeypatch.setattr(coursera_dl, "CourseraExtractor", FakeExtractor)
    monkeypatch.setattr(coursera_dl, "is_debug_run", lambda: False)

    calls = []

    def record_spit_json(modules, filename):
        calls.append((modules, filename))

    monkeypatch.setattr(coursera_dl, "spit_json", record_spit_json)

    args = make_args(cache_syllabus=True)

    error_occurred, completed = coursera_dl.download_on_demand_class(
        session=object(),
        args=args,
        class_name="fake-course",
    )

    assert error_occurred is False
    assert completed is False
    assert calls == [([], "fake-course-syllabus-parsed.json")]


def test_cookies_file_is_loaded_before_module_extraction(monkeypatch):
    session = object()
    calls = []

    class RecordingExtractor(FakeExtractor):
        def get_modules(self, *args, **kwargs):
            calls.append(("get_modules", args, kwargs))
            return False, []

    def record_get_cookies_for_class(*args, **kwargs):
        calls.append(("get_cookies_for_class", args, kwargs))

    monkeypatch.setattr(coursera_dl, "CourseraExtractor", RecordingExtractor)
    monkeypatch.setattr(coursera_dl, "get_cookies_for_class", record_get_cookies_for_class)
    monkeypatch.setattr(coursera_dl, "is_debug_run", lambda: False)

    args = make_args(cookies_file="cookies.txt")

    error_occurred, completed = coursera_dl.download_on_demand_class(
        session=session,
        args=args,
        class_name="fake-course",
    )

    assert error_occurred is False
    assert completed is False
    assert calls[0] == (
        "get_cookies_for_class",
        (session, "fake-course"),
        {"cookies_file": "cookies.txt"},
    )
    assert calls[1][0] == "get_modules"


def test_default_download_root_stays_empty_for_regular_course():
    args = make_args()

    assert coursera_dl.get_default_download_root(args) == ""


def test_default_download_root_prefers_explicit_path():
    args = make_args(path="downloads")

    assert coursera_dl.get_default_download_root(
        args,
        "https://www.coursera.org/specializations/machine-learning-introduction",
    ) == "downloads"


def test_default_download_root_uses_slug_from_coursera_url():
    args = make_args()

    assert coursera_dl.get_default_download_root(
        args,
        "https://www.coursera.org/specializations/machine-learning-introduction",
    ) == "machine-learning-introduction"
