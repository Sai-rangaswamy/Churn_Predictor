import { createRouter, createWebHistory } from "vue-router"

import Upload from "../views/Upload.vue"
import Dashboard from "../views/Dashboard.vue"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "upload",
      component: Upload,
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: Dashboard,
    },
  ],
})

export default router