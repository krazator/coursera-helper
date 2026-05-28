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