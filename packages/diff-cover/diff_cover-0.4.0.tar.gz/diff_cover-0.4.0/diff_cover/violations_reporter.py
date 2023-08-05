"""
Classes for querying the information in a test coverage report.
"""
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from collections import namedtuple, defaultdict
import re
import subprocess
import sys
import six


Violation = namedtuple('Violation', 'line, message')


class BaseViolationReporter(object):
    """
    Query information from a coverage report.
    """

    __metaclass__ = ABCMeta

    def __init__(self, name):
        """
        Provide a name for the coverage report, which will be included
        in the generated diff report.
        """
        self._name = name

    @abstractmethod
    def violations(self, src_path):
        """
        Return a list of Violations recorded in `src_path`.
        """
        pass

    def measured_lines(self, src_path):
        """
        Return a list of the lines in src_path that were measured
        by this reporter.

        Some reporters will always consider all lines in the file "measured".
        As an optimization, such violation reporters
        can return `None` to indicate that all lines are measured.
        The diff reporter generator will then use all changed lines
        provided by the diff.
        """
        return None

    def name(self):
        """
        Retrieve the name of the report, which may be
        included in the generated diff coverage report.

        For example, `name()` could return the path to the coverage
        report file or the type of reporter.
        """
        return self._name


class XmlCoverageReporter(BaseViolationReporter):
    """
    Query information from a Cobertura XML coverage report.
    """

    def __init__(self, xml_roots, git_path):
        """
        Load the Cobertura XML coverage report represented
        by the lxml.etree with root element `xml_root`.
        """
        super(XmlCoverageReporter, self).__init__("XML")
        self._xml_roots = xml_roots

        # Create a dict to cache violations dict results
        # Keys are source file paths, values are output of `violations()`
        self._info_cache = defaultdict(list)
        self._git_path = git_path

    def _get_src_path_line_nodes(self, xml_document, src_path):
        """
        Returns a list of nodes containing line information for `src_path`
        in `xml_document`.

        If file is not present in `xml_document`, return None
        """

        # Remove git_root from src_path for searching the correct filename
        # If cwd is `/home/user/work/diff-cover/diff_cover`
        # and src_path is `diff_cover/violations_reporter.py`
        # search for `violations_reporter.py`
        src_rel_path = self._git_path.relative_path(src_path)

        # If cwd is `/home/user/work/diff-cover/diff_cover`
        # and src_path is `other_package/some_file.py`
        # search for `/home/user/work/diff-cover/other_package/some_file.py`
        src_abs_path = self._git_path.absolute_path(src_path)

        xpath_template = ".//class[@filename='{0}']/lines/line"
        xpath = None

        src_node_xpath = ".//class[@filename='{0}']".format(src_rel_path)
        if xml_document.find(src_node_xpath) is not None:
            xpath = xpath_template.format(src_rel_path)

        src_node_xpath = ".//class[@filename='{0}']".format(src_abs_path)
        if xml_document.find(src_node_xpath) is not None:
            xpath = xpath_template.format(src_abs_path)

        if xpath is None:
            return None

        return xml_document.findall(xpath)

    def _cache_file(self, src_path):
        """
        Load the data from `self._xml_roots`
        for `src_path`, if it hasn't been already.
        """
        # If we have not yet loaded this source file
        if src_path not in self._info_cache:
            # We only want to keep violations that show up in each xml source.
            # Thus, each time, we take the intersection.  However, to do this
            # we must treat the first time as a special case and just add all
            # the violations from the first xml report.
            violations = None

            # A line is measured if it is measured in any of the reports, so
            # we take set union each time and can just start with the empty set
            measured = set()

            # Loop through the files that contain the xml roots
            for xml_document in self._xml_roots:
                line_nodes = self._get_src_path_line_nodes(xml_document,
                                                           src_path)

                if line_nodes is None:
                    continue

                # First case, need to define violations initially
                if violations is None:
                    violations = set(
                        Violation(int(line.get('number')), None)
                        for line in line_nodes
                        if int(line.get('hits', 0)) == 0)

                # If we already have a violations set,
                # take the intersection of the new
                # violations set and its old self
                else:
                    violations = violations & set(
                        Violation(int(line.get('number')), None)
                        for line in line_nodes
                        if int(line.get('hits', 0)) == 0
                    )

                # Measured is the union of itself and the new measured
                measured = measured | set(
                    int(line.get('number')) for line in line_nodes
                )

            # If we don't have any information about the source file,
            # don't report any violations
            if violations is None:
                violations = set()

            self._info_cache[src_path] = (violations, measured)

    def violations(self, src_path):
        """
        See base class comments.
        """

        self._cache_file(src_path)

        # Yield all lines not covered
        return self._info_cache[src_path][0]

    def measured_lines(self, src_path):
        """
        See base class docstring.
        """
        self._cache_file(src_path)
        return self._info_cache[src_path][1]


class BaseQualityReporter(BaseViolationReporter):
    """
    Abstract class to report code quality
    information, using `COMMAND`
    (provided by subclasses).
    """
    COMMAND = ''
    OPTIONS = []

    # Encoding of the stdout from the command
    # This is application-dependent
    STDOUT_ENCODING = 'utf-8'

    # A list of filetypes to run on.
    EXTENSIONS = []

    def __init__(self, name, input_reports):
        """
        Create a new quality reporter.

        `name` is an identifier for the reporter
        (usually the name of the tool used to generate
        the report).

        `input_reports` is an list of
        file-like objects representing pre-generated
        violation reports.  The list can be empty.

        If these are provided, the reporter will
        use the pre-generated reports instead of invoking
        the tool directly.
        """
        super(BaseQualityReporter, self).__init__(name)
        self._info_cache = defaultdict(list)

        # If we've been given input report files, use those
        # to get the source information
        if len(input_reports) > 0:
            self.use_tool = False
            self._load_reports(input_reports)
        else:
            self.use_tool = True

    def violations(self, src_path):
        """
        See base class comments.
        """
        # If we've been given pre-generated pylint/pep8 reports,
        # then we've already loaded everything we need into the cache.
        # Otherwise, call pylint/pep8 ourselves
        if self.use_tool:
            if not any(src_path.endswith(ext) for ext in self.EXTENSIONS):
                return []
            if src_path not in self._info_cache:
                output = self._run_command(src_path)
                violations_dict = self._parse_output(output, src_path)
                self._update_cache(violations_dict)

        # Return the cached violation info
        return self._info_cache[src_path]

    def _load_reports(self, report_files):
        """
        Load pre-generated pep8/pylint reports into
        the cache.

        `report_files` is a list of open file-like objects.
        """
        for file_handle in report_files:
            # Convert to unicode, replacing unreadable chars
            contents = file_handle.read().decode(self.STDOUT_ENCODING,
                                                 'replace')
            violations_dict = self._parse_output(contents)
            self._update_cache(violations_dict)

    def _update_cache(self, violations_dict):
        """
        Append violations in `violations_dict` to the cache.
        `violations_dict` must have the form:

            {
                SRC_PATH: [Violation, ]
            }
        """
        for src_path, violations in six.iteritems(violations_dict):
            self._info_cache[src_path].extend(violations)

    def _run_command(self, src_path):
        """
        Run the quality command and return its output as a unicode string.
        """
        # Encode the path using the filesystem encoding, determined at runtime
        encoding = sys.getfilesystemencoding()
        command = [self.COMMAND] + self.OPTIONS + [src_path.encode(encoding)]

        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
        except OSError:
            sys.stderr.write(" ".join([cmd.decode(encoding)
                                       if isinstance(cmd, bytes) else cmd
                                       for cmd in command]))
            raise

        if stderr:
            raise QualityReporterError(stderr.decode(encoding))

        return stdout.strip().decode(self.STDOUT_ENCODING, 'replace')

    @abstractmethod
    def _parse_output(self, output, src_path=None):
        """
        Parse the output of this reporter
        command into a dict of the form:

            {
                SRC_PATH: [Violation, ]
            }

        where `SRC_PATH` is the path to the source file
        containing the violations, and the value is
        a list of violations.

        If `src_path` is provided, return information
        just for that source.
        """
        pass


class Pep8QualityReporter(BaseQualityReporter):
    """
    Report PEP8 violations.
    """
    COMMAND = 'pep8'

    EXTENSIONS = ['py']
    VIOLATION_REGEX = re.compile(r'^([^:]+):(\d+).*([EW]\d{3}.*)$')

    def _parse_output(self, output, src_path=None):
        """
        See base class docstring.
        """
        violations_dict = defaultdict(list)

        for line in output.split('\n'):

            match = self.VIOLATION_REGEX.match(line)

            # Ignore any line that isn't a violation
            if match is not None:
                pep8_src, line_number, message = match.groups()

                # If we're looking for a particular source,
                # filter out all other sources
                if src_path is None or src_path == pep8_src:
                    violation = Violation(int(line_number), message)
                    violations_dict[pep8_src].append(violation)

        return violations_dict


class PylintQualityReporter(BaseQualityReporter):
    """
    Report Pylint violations.
    """
    COMMAND = 'pylint'
    MODERN_OPTIONS = ['--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"']
    LEGACY_OPTIONS = ['-f', 'parseable', '--reports=no', '--include-ids=y']
    OPTIONS = MODERN_OPTIONS
    EXTENSIONS = ['py']

    # Match lines of the form:
    # path/to/file.py:123: [C0111] Missing docstring
    # path/to/file.py:456: [C0111, Foo.bar] Missing docstring
    VIOLATION_REGEX = re.compile(r'^([^:]+):(\d+): \[(\w+),? ?([^\]]*)] (.*)$')

    def _run_command(self, src_path):
        try:
            return super(PylintQualityReporter, self)._run_command(src_path)
        except QualityReporterError as report_error:
            # Support earlier pylint version (< 1)
            if "no such option: --msg-template" in report_error.message:
                self.OPTIONS = self.LEGACY_OPTIONS
                return super(PylintQualityReporter, self)._run_command(src_path)
            else:
                raise

    def _parse_output(self, output, src_path=None):
        """
        See base class docstring.
        """
        violations_dict = defaultdict(list)

        for line in output.split('\n'):
            match = self.VIOLATION_REGEX.match(line)

            # Ignore any line that isn't matched
            # (for example, snippets from the source code)
            if match is not None:

                pylint_src_path, line_number, pylint_code, function_name, message = match.groups()

                # If we're looking for a particular source file,
                # ignore any other source files.
                if src_path is None or src_path == pylint_src_path:

                    if function_name:
                        error_str = u"{0}: {1}: {2}".format(pylint_code, function_name, message)
                    else:
                        error_str = u"{0}: {1}".format(pylint_code, message)

                    violation = Violation(int(line_number), error_str)
                    violations_dict[pylint_src_path].append(violation)

        return violations_dict


class QualityReporterError(Exception):
    """
    A quality reporter command produced an error.
    """
    def __init__(self, message):
        self.message = message
