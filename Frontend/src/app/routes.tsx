import { createBrowserRouter } from "react-router";
import { AccessGate } from "./components/AccessGate";
import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { MenuPage } from "./pages/MenuPage";
import { FavoritesPage } from "./pages/FavoritesPage";
import { AboutPage } from "./pages/AboutPage";
import { SeoDocumentView } from "./pages/SeoDocumentView";
import { SlugPage } from "./pages/SlugPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: AccessGate,
    children: [
      { path: "login", Component: LoginPage },
      { path: "robots.txt", Component: SeoDocumentView },
      { path: "sitemap.xml", Component: SeoDocumentView },
      {
        Component: Layout,
        children: [
          { index: true, Component: HomePage },
          { path: "menu", Component: MenuPage },
          { path: "adisyon", Component: FavoritesPage },
          { path: "about", Component: AboutPage },
          { path: ":slug", Component: SlugPage },
        ],
      },
    ],
  },
]);
