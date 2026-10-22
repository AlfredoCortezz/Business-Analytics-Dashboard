import "@testing-library/jest-dom/vitest";

// Fija el idioma de la interfaz a español durante las pruebas para que las
// aserciones sobre textos sean deterministas (jsdom reporta idioma inglés).
localStorage.setItem("bad.language", "es");
