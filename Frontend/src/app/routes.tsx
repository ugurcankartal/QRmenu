import { createBrowserRouter } from "react-router";
import { AccessGate } from "./components/AccessGate";
import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { MenuPage } from "./pages/MenuPage";
import { FavoritesPage } from "./pages/FavoritesPage";
import { AboutPage } from "./pages/AboutPage";
import { SeoDocumentRedirect } from "./pages/SeoDocumentRedirect";
import { SlugPage } from "./pages/SlugPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: AccessGate,
    children: [
      { path: "login", Component: LoginPage },
      {
        Component: Layout,
        children: [
          { index: true, Component: HomePage },
          { path: "menu", Component: MenuPage },
          { path: "adisyon", Component: FavoritesPage },
          { path: "about", Component: AboutPage },
          { path: "robots.txt", Component: SeoDocumentRedirect },
          { path: "sitemap.xml", Component: SeoDocumentRedirect },
          { path: ":slug", Component: SlugPage },
        ],
      },
    ],
  },
]);
