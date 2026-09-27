import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { api } from "../api/client";

export function WorkspacesPage() {
  const qc = useQueryClient();
  const [name, setName] = useState("my-workspace");
  const list = useQuery({ queryKey: ["workspaces"], queryFn: api.listWorkspaces });
  const create = useMutation({
    mutationFn: () => api.createWorkspace({ name }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    create.mutate();
  }

  return (
    <section>
      <h1>Workspaces</h1>
      <p className="lede">Create and list workspaces for the current actor.</p>

      <form className="row" onSubmit={onSubmit}>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Workspace name"
        />
        <button className="primary" type="submit" disabled={create.isPending}>
          Create
        </button>
      </form>
      {create.isError && (
        <p className="error">{(create.error as Error).message}</p>
      )}

      {list.isLoading && <p>Loading…</p>}
      {list.isError && (
        <p className="error">{(list.error as Error).message}</p>
      )}
      {list.data && (
        <table>
          <thead>
            <tr>
              <th>Id</th>
              <th>Name</th>
              <th>Members</th>
            </tr>
          </thead>
          <tbody>
            {list.data.map((ws) => (
              <tr key={ws.id}>
                <td>
                  <code>{ws.id}</code>
                </td>
                <td>{ws.name}</td>
                <td>
                  {ws.members.map((m) => `${m.user_id}(${m.role})`).join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
