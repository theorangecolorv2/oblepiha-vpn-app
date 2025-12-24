import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { SubPage } from './pages/SubPage.tsx'
import { InfoPage } from './pages/InfoPage.tsx'

// Простой роутинг на основе pathname
function Router() {
  const path = window.location.pathname
  
  // Страница импорта подписки
  if (path === '/sub' || path === '/sub/') {
    return <SubPage />
  }
  
  // Страница информации (FAQ + условия использования)
  if (path === '/info' || path === '/info/') {
    return <InfoPage />
  }
  
  // Главное приложение
  return <App />
}

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
    <Router />
  </StrictMode>,
)

hideLoader()
