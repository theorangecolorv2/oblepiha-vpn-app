import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export function Button({ 
  children, 
  variant = 'primary', 
  disabled,
  className = '',
  ...props 
}: ButtonProps) {
  const baseStyles = 'w-full py-4 px-6 rounded-2xl font-semibold text-lg transition-all active:scale-[0.98] duration-200'
  
  const variants = {
    primary: disabled
      ? 'bg-chocolate/20 text-chocolate/40 cursor-not-allowed'
      : 'bg-primary text-white shadow-lg shadow-primary/30 hover:shadow-primary/40 hover:bg-[#d54d26]',
    secondary: 'bg-background-light text-chocolate hover:bg-white',
  }
  
  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
