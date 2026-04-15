import { defineConfig } from "vite";

export default defineConfig({
  plugins: [],
  server: {
    host: true,
    allowedHosts: ["user-b2473f16.dm-k8s.bluetext.dev"],
    port: 5173
  },
  build: {
    target: "es2020"
  }
});
