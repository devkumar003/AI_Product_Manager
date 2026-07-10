import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

describe("Card UI Components", () => {
  it("renders Card with children", () => {
    render(
      <Card data-testid="test-card">
        <span>Card Content</span>
      </Card>
    );
    const card = screen.getByTestId("test-card");
    expect(card).toBeDefined();
    expect(card.textContent).toBe("Card Content");
  });

  it("renders CardHeader and CardTitle correctly", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Active Projects</CardTitle>
          <CardDescription>From current workspace</CardDescription>
        </CardHeader>
      </Card>
    );
    expect(screen.getByText("Active Projects")).toBeDefined();
    expect(screen.getByText("From current workspace")).toBeDefined();
  });

  it("renders CardContent with dashboard stat values", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Spec Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <p data-testid="stat-value" className="text-3xl font-bold">12</p>
        </CardContent>
      </Card>
    );
    expect(screen.getByText("Spec Documents")).toBeDefined();
    expect(screen.getByTestId("stat-value").textContent).toBe("12");
  });

  it("applies custom className to Card", () => {
    render(
      <Card className="custom-class" data-testid="styled-card">
        Test
      </Card>
    );
    const card = screen.getByTestId("styled-card");
    expect(card.className).toContain("custom-class");
  });

  it("renders multiple stat cards as dashboard grid would", () => {
    const stats = [
      { name: "Active Projects", value: "5" },
      { name: "Spec Documents", value: "12" },
      { name: "Workspace Activities", value: "48" },
    ];
    render(
      <div data-testid="dashboard-grid">
        {stats.map((stat, idx) => (
          <Card key={idx}>
            <CardHeader>
              <CardTitle>{stat.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    );
    expect(screen.getByText("Active Projects")).toBeDefined();
    expect(screen.getByText("Spec Documents")).toBeDefined();
    expect(screen.getByText("Workspace Activities")).toBeDefined();
    expect(screen.getByText("5")).toBeDefined();
    expect(screen.getByText("12")).toBeDefined();
    expect(screen.getByText("48")).toBeDefined();
  });
});
