from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app
from backend.schemas import (
    RefineResponse,
    BreakdownResponse,
    PlanResponse,
    PlanOption,
    PlanStep,
    FinalStep,
)

client = TestClient(app)

# Mock data
mock_refine_response = RefineResponse(
    refinedIdea="Refined Idea that is definitely long enough to pass validation",
    questions=["Question 1", "Question 2"],
)

mock_breakdown_response = BreakdownResponse(
    plans=[
        PlanOption(
            name="Lean Plan",
            steps=[
                PlanStep(text="Step 1"),
                PlanStep(text="Step 2"),
                PlanStep(text="Step 3"),
            ],
        ),
        PlanOption(
            name="Thorough Plan",
            steps=[
                PlanStep(text="Step 1"),
                PlanStep(text="Step 2"),
                PlanStep(text="Step 3"),
                PlanStep(text="Step 4"),
            ],
        ),
    ]
)

mock_plan_response = PlanResponse(
    optionName="Lean Plan",
    steps=[
        FinalStep(text="Step 1", duration_minutes=15),
        FinalStep(text="Step 2", duration_minutes=30),
        FinalStep(text="Step 3", duration_minutes=15),
    ],
    total_duration=60,
    parked_indices=[],
)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("backend.main.refine_with_lang")
def test_refine_endpoint(mock_refine):
    mock_refine.return_value = mock_refine_response

    response = client.post("/refine", json={"idea": "Test Idea"})

    assert response.status_code == 200
    data = response.json()
    assert (
        data["refinedIdea"]
        == "Refined Idea that is definitely long enough to pass validation"
    )
    assert len(data["questions"]) == 2


@patch("backend.main.breakdown_with_lc")
def test_breakdown_endpoint(mock_breakdown):
    mock_breakdown.return_value = mock_breakdown_response

    response = client.post(
        "/breakdown", json={"definition": "Test Definition", "max_steps": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["plans"]) == 2
    assert data["plans"][0]["name"] == "Lean Plan"


@patch("backend.main.plan_with_lc")
def test_plan_endpoint(mock_plan):
    # plan_with_lc is async, so we need to mock it as an async function return
    future = MagicMock()
    future.__await__ = MagicMock(return_value=iter([mock_plan_response]))
    # Alternatively, just set return_value to the object if the test client handles async mocking,
    # but patch needs careful handling for async.
    # Simpler approach: use AsyncMock if available or just return the object if not awaited in the route?
    # The route awaits it: out = await plan_with_lc(req)
    # So we need an AsyncMock.

    # Since we are using standard unittest.mock, we can configure it:
    async def async_return(*args, **kwargs):
        return mock_plan_response

    mock_plan.side_effect = async_return

    response = client.post(
        "/plan",
        json={
            "optionName": "Lean Plan",
            "steps": [{"text": "Step 1"}, {"text": "Step 2"}, {"text": "Step 3"}],
            "total_minutes": 60,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_duration"] == 60
    assert len(data["steps"]) == 3
