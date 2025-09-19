from pyomo.environ import *
from dataclasses import dataclass

# Input data

# Time constraint
max_minutes_per_day = 15

# ============================================================================
@dataclass
class BuildModel:
    chores: list
    durations: dict
    days_needed: dict
    max_minutes_per_day: int

    # ------------------------------------------------------------------------
    def create_model(self):
        self.model = ConcreteModel()
        self.model.DAYS = RangeSet(1, 7)
        self.model.CHORES = Set(initialize=self.chores)
        self.model.x = Var(self.model.CHORES, self.model.DAYS, domain=Binary)
        return self

    # ------------------------------------------------------------------------
    def add_constraints(self):
        def time_constraint(model, d):
            rule = (
                sum(self.durations[c] * model.x[c, d] for c in model.CHORES) 
                <= self.max_minutes_per_day
            )
            return rule

        self.model.time_constraint = Constraint(
            self.model.DAYS, rule=time_constraint
        )

        def chore_count_constraint(model, c):
            rule = (
                sum(model.x[c, d] for d in model.DAYS) == self.days_needed[c]
            )
            return rule

        self.model.chore_count_constraint = Constraint(
            self.model.CHORES, rule=chore_count_constraint
        )
        return self
    
    def set_objective(self):
        self.model.obj = Objective(expr=0)
        return self
    
    def solve(self):
        solver = SolverFactory('cplex_direct')
        solver.solve(self.model)
        return self