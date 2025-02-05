from collections import defaultdict
from cp2_types import CourseInfo, CourseRequest, ScheduleParams, Requirement
from solver import generate_schedule
import pytest

def test_empty(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=1,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    for sem in schedule:
        assert len(sem) == 0


def test_requirement_one_course(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(courses=['CIS-120'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert len(schedule[0]) == 0
    assert schedule[1] == ['CIS-120']


def test_requirement_one_category(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(categories=['MATH@SEAS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert len(schedule[0]) == 0
    assert len(schedule[1]) == 1
    course_id = schedule[1][0]
    course_info = next(info for info in sample_courses_info if info['id'] == course_id)
    assert any(req['id'] == 'MATH@SEAS' for req in course_info['requirements'])
    

def test_requirement_one_dept(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(depts=['CIS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert len(schedule[0]) == 0
    assert len(schedule[1]) == 1
    course_id = schedule[1][0]
    assert course_id.startswith('CIS')


def test_requirement_one_course_not_exists(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(courses=['CIS-420'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert not generate_schedule(sample_courses_info, [], params)


def test_requirement_one_category_not_exists(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(categories=['FUN@SEAS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert not generate_schedule(sample_courses_info, [], params)


def test_requirement_one_dept_not_exists(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(depts=['OMG'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert not generate_schedule(sample_courses_info, [], params)


def test_requirement_same_course_not_allowed(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(courses=['CIS-120']),
            Requirement(courses=['CIS-120'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert not generate_schedule(sample_courses_info, [], params)


def test_requirement_two_courses(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(courses=['CIS-120']),
            Requirement(courses=['CIS-160'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert len(schedule[0]) == 0
    assert not (set(schedule[1]) ^ {'CIS-120', 'CIS-160'})


def test_requirement_two_depts_same(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(depts=['CIS']),
            Requirement(depts=['CIS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert len(schedule[0]) == 0
    assert len(schedule[1]) == 2
    # Courses should not be the same
    assert len(set(schedule[1])) == 2
    for course in schedule[1]:
        assert course.startswith('CIS')


def test_requirement_two_depts_different(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[[
            Requirement(depts=['CIS']),
            Requirement(depts=['MATH'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert len(schedule[0]) == 0
    assert len(schedule[1]) == 2
    cis, math = sorted(schedule[1])
    assert cis.startswith('CIS')
    assert math.startswith('MATH')


def test_more_requirements_than_slots(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        max_courses_per_semester=1,
        requirement_blocks=[[
            Requirement(depts=['CIS']),
            Requirement(depts=['CIS']),
            Requirement(depts=['MATH']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert not generate_schedule(sample_courses_info, [], params)


def test_one_course_request(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    course_requests = [
        CourseRequest('CIS-120', 1)
    ]
    assert (soln := generate_schedule(sample_courses_info, course_requests, params))
    schedule, _ = soln
    # No courses should be scheduled in the precollege semester
    assert len(schedule[0]) == 0
    assert schedule[1] == ['CIS-120']


def test_invalid_course_request(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    course_requests = [
        CourseRequest('CIS-120', 2)
    ]
    with pytest.raises(KeyError):
        assert not generate_schedule(sample_courses_info, course_requests, params)


def test_one_course_request_precollege(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    course_requests = [
        CourseRequest('CIS-120', 0)
    ]
    assert (soln := generate_schedule(sample_courses_info, course_requests, params))
    schedule, _ = soln
    assert schedule[0] == ['CIS-120']
    assert len(schedule[1]) == 0


def test_prerequisites_feasible(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        max_courses_per_semester=1,
        requirement_blocks=[[
            Requirement(courses=['CIS-262']),
            Requirement(courses=['CIS-160']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )

    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, _ = soln
    assert schedule[1] == ['CIS-160']
    assert schedule[2] == ['CIS-262']


def test_prerequisites_infeasible(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        max_courses_per_semester=1,
        requirement_blocks=[[
            Requirement(courses=['CIS-121']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    assert not generate_schedule(sample_courses_info, [], params)


def test_prerequisites_requests_infeasible(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        max_courses_per_semester=1,
        requirement_blocks=[[
            Requirement(courses=['CIS-262']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
    )
    course_requests = [
        CourseRequest('CIS-262', 1)
    ]
    assert not generate_schedule(sample_courses_info, course_requests, params)


def test_double_count(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=1,
        requirement_blocks=[
            [Requirement(categories=['MATH@SEAS'])],
            [Requirement(categories=['FGE@WH'])],
        ],
        # Can double count once
        max_double_counts=defaultdict(lambda: 1),
    )

    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, counts_for = soln
    assert len(schedule[0]) == 0
    assert len(schedule[1]) == 1
    course_id = schedule[1][0]
    info = next(info for info in sample_courses_info if info['id'] == course_id)
    req_ids = [req['id'] for req in info['requirements']]

    assert 'MATH@SEAS' in req_ids
    assert 'FGE@WH' in req_ids
    assert counts_for[course_id] == [(0, 0), (1, 0)]


def test_double_count_infinite_one_semester(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=2,
        requirement_blocks=[
            [Requirement(courses=['CIS-120']), Requirement(courses=['CIS-160'])],
            [Requirement(courses=['CIS-160']), Requirement(courses=['CIS-120'])],
        ],
        # Can double count infinite times
        max_double_counts=defaultdict(lambda: None),
    )

    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, counts_for = soln
    assert len(schedule[0]) == 0
    assert not set(schedule[1]) ^ {'CIS-120', 'CIS-160'}
    assert counts_for['CIS-120'] == [(0, 0), (1, 1)]
    assert counts_for['CIS-160'] == [(0, 1), (1, 0)]


def test_double_count_infinite_multiple_semesters(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        max_courses_per_semester=1,
        requirement_blocks=[
            [Requirement(courses=['CIS-160']), Requirement(courses=['CIS-262'])],
            [Requirement(courses=['CIS-262']), Requirement(courses=['CIS-160'])],
        ],
        # Can double count infinite times
        max_double_counts=defaultdict(lambda: None),
    )

    assert (soln := generate_schedule(sample_courses_info, [], params))
    schedule, counts_for = soln
    assert len(schedule[0]) == 0
    assert schedule[1] == ['CIS-160']
    assert schedule[2] == ['CIS-262']
    assert counts_for['CIS-160'] == [(0, 0), (1, 1)]
    assert counts_for['CIS-262'] == [(0, 1), (1, 0)]


def test_no_double_count(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=1,
        requirement_blocks=[
            [Requirement(categories=['MATH@SEAS'])],
            [Requirement(categories=['FGE@WH'])],
        ],
        # No double counting
        max_double_counts=defaultdict(lambda: 0),
    )

    assert not generate_schedule(sample_courses_info, [], params)


def test_no_triple_count(sample_courses_info: list[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        max_courses_per_semester=1,
        requirement_blocks=[
            [Requirement(categories=['MATH@SEAS'])],
            [Requirement(categories=['FGE@WH'])],
            [Requirement(categories=['MFR@SAS'])],
        ],
        # Infinite double counting but we can never triple count
        max_double_counts=defaultdict(lambda: None),
    )

    assert not generate_schedule(sample_courses_info, [], params)


# TODO: left to test
# - multiple requirement blocks
# - multiple requirements per block
# - multiple requests
# - more complex prerequisites
# - more complex double counting
# - requirements that can be satisfied in multiple ways
# - requirements that require both category and department to satisfy