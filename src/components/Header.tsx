interface HeaderProps {
  firstName: string
}
// Шапка
export function Header({ firstName }: HeaderProps) {
  return (
    <header className="flex flex-col mb-4">
      {/* Brand Lockup */}
      <div className="flex items-center gap-2.5 mb-3">
        <img 
          src="/logo.webp" 
          alt="Облепиха VPN" 
          className="h-11 w-auto"
        />
        <span className="text-chocolate text-base font-bold tracking-tight">
          Облепиха VPN
        </span>
      </div>
      
      {/* Greeting */}
      <h1 className="text-chocolate text-xl font-bold leading-tight">
        Привет, {firstName}
      </h1>
    </header>
  )
}
