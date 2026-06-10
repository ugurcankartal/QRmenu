import { RouterProvider } from "react-router";
import { FrontendAuthProvider } from "./context/FrontendAuthContext";
import { SiteAccessProvider } from "./context/SiteAccessContext";
import { router } from "./routes";

export default function App() {
  return (
    <SiteAccessProvider>
      <FrontendAuthProvider>
        <RouterProvider router={router} />
      </FrontendAuthProvider>
    </SiteAccessProvider>
  );
}