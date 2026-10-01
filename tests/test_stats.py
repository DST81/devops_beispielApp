def test_stats_empty_board(client):
    response = client.get("/api/tasks/stats")

    assert response.status_code == 200
    assert response.get_json() == {
        "total": 0,
        "done": 0,
        "open": 0,
    }


def test_stats_mixed_tasks(client):
    task1 = client.post(
        "/api/tasks",
        json={"title": "Task 1"},
    ).get_json()

    client.post(
        "/api/tasks",
        json={"title": "Task 2"},
    )

    task3 = client.post(
        "/api/tasks",
        json={"title": "Task 3"},
    ).get_json()

    client.put(
        f"/api/tasks/{task1['id']}",
        json={"done": True},
    )

    client.put(
        f"/api/tasks/{task3['id']}",
        json={"done": True},
    )

    response = client.get("/api/tasks/stats")

    assert response.status_code == 200
    assert response.get_json() == {
        "total": 3,
        "done": 2,
        "open": 1,
    }


def test_stats_all_tasks_done(client):
    task1 = client.post(
        "/api/tasks",
        json={"title": "Task 1"},
    ).get_json()

    task2 = client.post(
        "/api/tasks",
        json={"title": "Task 2"},
    ).get_json()

    client.put(
        f"/api/tasks/{task1['id']}",
        json={"done": True},
    )

    client.put(
        f"/api/tasks/{task2['id']}",
        json={"done": True},
    )

    response = client.get("/api/tasks/stats")

    assert response.status_code == 200
    assert response.get_json() == {
        "total": 2,
        "done": 2,
        "open": 0,
    }
