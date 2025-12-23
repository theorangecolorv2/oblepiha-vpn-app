import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Скрываем лоадер после загрузки шрифтов и рендера
function hideLoader() {
  const loader = document.getElementById('loader')
  if (loader) {
    // Минимум 500ms показываем лоадер + ждём загрузки шрифтов
    Promise.all([
      document.fonts.ready,
      new Promise(resolve => setTimeout(resolve, 500))
    ]).then(() => {
      loader.classList.add('hidden')
      // Удаляем из DOM после анимации
      setTimeout(() => loader.remove(), 300)
    })
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

hideLoader()
