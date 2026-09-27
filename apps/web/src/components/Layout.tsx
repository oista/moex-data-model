import { NavLink, Outlet } from "react-router-dom";
import { useState } from "react";
import { getActor } from "../api/client";
import { ActorBar } from "./ActorBar";

export function Layout() {
  const [actor, setActorState] = useState(getActor);

  return (
    <div className="shell">
      <nav className="side">
        <div className="brand">MOEX Workbench</div>
        <NavLink to="/" end>
          Dashboard
        </NavLink>
        <NavLink to="/workspaces">Workspaces</NavLink>
        <NavLink to="/models">Models</NavLink>
        <p className="lede" style={{ marginTop: "1rem", fontSize: "0.85rem" }}>
          Signed in as <strong>{actor}</strong>
        </p>
        <ActorBar onChange={setActorState} />
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
