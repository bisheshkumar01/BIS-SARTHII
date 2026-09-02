import { forwardRef } from 'react'
import { ArrowRight } from 'lucide-react'
import { cn } from '../../lib/cn.js'

/*
  Adapted from MagicUI's "Interactive Hover Button" (21st.dev, dillionverma), converted from
  TSX to JSX and re-pointed at the BIS palette — the original uses shadcn's bg-background /
  bg-primary tokens, which don't exist in this project's theme.

  The effect: the label slides out to the right while a dot in the lower-left inflates to fill
  the button, and a second label slides in behind it with an arrow. Pure CSS transitions on a
  group — no framer-motion.
*/

/*
  Variants rather than caller-supplied overrides. `cn` here is a plain join, not tailwind-merge,
  so passing e.g. `bg-saffron-500` alongside a variant's `bg-white/5` leaves BOTH classes on the
  element and the winner is decided by stylesheet order, not argument order. Every background,
  border and text colour therefore lives in exactly one variant.
*/
const VARIANTS = {
  // Solid saffron: the primary CTA. The dot inflates in a deeper saffron, so the fill reads as
  // the same button pressing forward rather than as a different colour arriving.
  solid: {
    base: 'border-transparent bg-saffron-500 text-white shadow-lg shadow-saffron-500/25',
    dot: 'bg-saffron-600',
    reveal: 'text-white',
  },
  // White pill for light sections.
  primary: {
    base: 'border-saffron-500/30 bg-white text-navy-900',
    dot: 'bg-saffron-500',
    reveal: 'text-white',
  },
  // Translucent pill on the navy hero, filling with saffron.
  onDark: {
    base: 'border-white/20 bg-white/5 text-white',
    dot: 'bg-saffron-500',
    reveal: 'text-white',
  },
}

const InteractiveHoverButton = forwardRef(function InteractiveHoverButton(
  { text = 'Button', variant = 'solid', className, ...props },
  ref,
) {
  const v = VARIANTS[variant] ?? VARIANTS.solid

  return (
    <button
      ref={ref}
      className={cn(
        'group relative cursor-pointer overflow-hidden rounded-full border px-7 py-3.5',
        'text-base font-semibold transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-saffron-400 focus-visible:ring-offset-2',
        v.base,
        className,
      )}
      {...props}
    >
      {/* Outgoing label. */}
      <span className="relative z-20 inline-block transition-all duration-300 group-hover:translate-x-8 group-hover:opacity-0">
        {text}
      </span>

      {/* Incoming label, waiting off to the left. */}
      <span
        className={cn(
          'absolute inset-0 z-20 flex translate-x-8 items-center justify-center gap-2',
          'opacity-0 transition-all duration-300 group-hover:translate-x-0 group-hover:opacity-100',
          v.reveal,
        )}
      >
        {text}
        <ArrowRight className="h-4 w-4" />
      </span>

      {/* The dot that inflates into the fill. scale-[1.8] guarantees it covers the corners. */}
      <span
        className={cn(
          'absolute left-[20%] top-[40%] z-10 h-2 w-2 rounded-lg transition-all duration-300',
          'group-hover:left-0 group-hover:top-0 group-hover:h-full group-hover:w-full group-hover:scale-[1.8]',
          v.dot,
        )}
      />
    </button>
  )
})

export default InteractiveHoverButton
