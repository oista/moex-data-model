import { useState } from "react";
import { getActor, setActor } from "../api/client";

type Props = { onChange?: (actor: string) => void };

export function ActorBar({ onChange }: Props) {
  const [value, setValue] = useState(getActor);

  function save() {
    setActor(value);
    onChange?.(getActor());
  }

  return (
    <div className="actor-bar">
      <label htmlFor="actor">Actor</label>
      <input
        id="actor"
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={save}
        onKeyDown={(e) => {
          if (e.key === "Enter") save();
        }}
      />
    </div>
  );
}
