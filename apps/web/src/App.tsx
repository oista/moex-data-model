import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { DiagramPage } from "./pages/DiagramPage";
import { EditorPage } from "./pages/EditorPage";
import { ImportWizardPage } from "./pages/ImportWizardPage";
import { ModelDetailPage } from "./pages/ModelDetailPage";
import { ModelsPage } from "./pages/ModelsPage";
import { ValidationPage } from "./pages/ValidationPage";
import { WorkspacesPage } from "./pages/WorkspacesPage";

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="workspaces" element={<WorkspacesPage />} />
        <Route
          path="workspaces/:workspaceId/import"
          element={<ImportWizardPage />}
        />
        <Route path="models" element={<ModelsPage />} />
        <Route path="models/trading/edit" element={<EditorPage />} />
        <Route path="models/trading/diagram" element={<DiagramPage />} />
        <Route path="models/:slug" element={<ModelDetailPage />} />
        <Route path="models/:slug/validate" element={<ValidationPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
