/**
 * Compass-in-shield mark: "shield" nods to BIS's regulatory trust,
 * the compass needle nods to SARTHI's job — guiding you to the right standard.
 */
export default function Logo({ className = 'h-8 w-8' }) {
  return (
    <svg viewBox="0 0 40 40" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
      <path
        d="M20 2 L36 8 V19 C36 29 29.5 35.5 20 38 C10.5 35.5 4 29 4 19 V8 Z"
        fill="var(--color-navy-800)"
      />
      <path
        d="M20 2 L36 8 V19 C36 29 29.5 35.5 20 38 C10.5 35.5 4 29 4 19 V8 Z"
        stroke="var(--color-saffron-500)"
        strokeWidth="1.5"
      />
      <circle cx="20" cy="19" r="9.5" stroke="var(--color-saffron-400)" strokeWidth="1.3" fill="none" />
      <path d="M20 12.5 L23 19 L20 25.5 L17 19 Z" fill="var(--color-saffron-500)" />
      <circle cx="20" cy="19" r="1.4" fill="var(--color-paper-50)" />
    </svg>
  )
}
