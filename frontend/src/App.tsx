import { Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { HomePage } from "./pages/HomePage";
import { EventsListPage } from "./pages/EventsListPage";
import { EventDetailsPage } from "./pages/EventDetailsPage";
import { CalendarPage } from "./pages/CalendarPage";
import { OrganizerLoginPage } from "./pages/OrganizerLoginPage";
import { AdminLoginPage } from "./pages/AdminLoginPage";
import { StudentLoginPage } from "./pages/StudentLoginPage";
import { StudentDashboardPage } from "./pages/StudentDashboardPage";
import { OrganizerDashboardPage } from "./pages/OrganizerDashboardPage";
import { AdminDashboardPage } from "./pages/AdminDashboardPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import { MyRegistrationsPage } from "./pages/student/MyRegistrationsPage";
import { RecommendationsPage } from "./pages/student/RecommendationsPage";
import { MyEventsPage } from "./pages/organizer/MyEventsPage";
import { EventFormPage } from "./pages/organizer/EventFormPage";
import { ParticipantsPage } from "./pages/organizer/ParticipantsPage";
import { MaterialsPage } from "./pages/organizer/MaterialsPage";
import { SubmitForApprovalPage } from "./pages/organizer/SubmitForApprovalPage";
import { PendingApprovalsPage } from "./pages/admin/PendingApprovalsPage";
import { OrganizerManagementPage } from "./pages/admin/OrganizerManagementPage";
import { ReportsPage } from "./pages/admin/ReportsPage";
import { ScrapingPage } from "./pages/admin/ScrapingPage";
import { AuthCallbackPage } from "./pages/AuthCallbackPage";
import { EventsManagementPage } from "./pages/admin/EventsManagementPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/events" element={<EventsListPage />} />
        <Route path="/events/:id" element={<EventDetailsPage />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/login/student" element={<StudentLoginPage />} />
        <Route path="/login/organizer" element={<OrganizerLoginPage />} />
        <Route path="/login/admin" element={<AdminLoginPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route
          path="/student"
          element={
            <ProtectedRoute roles={["student"]}>
              <StudentDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/registrations"
          element={
            <ProtectedRoute roles={["student"]}>
              <MyRegistrationsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/recommendations"
          element={
            <ProtectedRoute roles={["student"]}>
              <RecommendationsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizer"
          element={
            <ProtectedRoute roles={["organizer"]}>
              <OrganizerDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizer/events"
          element={
            <ProtectedRoute roles={["organizer"]}>
              <MyEventsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizer/create"
          element={
            <ProtectedRoute roles={["organizer"]}>
              <EventFormPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizer/events/:id/edit"
          element={
            <ProtectedRoute roles={["organizer"]}>
              <EventFormPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizer/events/:id/participants"
          element={
            <ProtectedRoute roles={["organizer"]}>
              <ParticipantsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizer/events/:id/materials"
          element={
            <ProtectedRoute roles={["organizer"]}>
              <MaterialsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/organizer/events/:id/submit"
          element={
            <ProtectedRoute roles={["organizer"]}>
              <SubmitForApprovalPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/pending"
          element={
            <ProtectedRoute roles={["admin"]}>
              <PendingApprovalsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/organizers"
          element={
            <ProtectedRoute roles={["admin"]}>
              <OrganizerManagementPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/events"
          element={
            <ProtectedRoute roles={["admin"]}>
              <EventsManagementPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/reports"
          element={
            <ProtectedRoute roles={["admin"]}>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/scraping"
          element={
            <ProtectedRoute roles={["admin"]}>
              <ScrapingPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
