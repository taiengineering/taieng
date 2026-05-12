/**
 * App 라우터에 병합 예시
 * npm i react-router-dom
 */
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { PartnerLandingPage } from './PartnerLandingPage';
import { RepairPartnerRegisterPage } from './RepairPartnerRegisterPage';
import { InspectorPartnerRegisterPage } from './InspectorPartnerRegisterPage';
import { SafetyAgencyRegisterPage } from './SafetyAgencyRegisterPage';

export function PartnerRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/partners" element={<PartnerLandingPage />} />
        <Route path="/partners/repair/register" element={<RepairPartnerRegisterPage />} />
        <Route path="/partners/inspector/register" element={<InspectorPartnerRegisterPage />} />
        <Route path="/partners/safety-agency/register" element={<SafetyAgencyRegisterPage />} />
        <Route path="*" element={<Navigate to="/partners" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
