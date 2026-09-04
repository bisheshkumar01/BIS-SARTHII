import { useRef, useCallback } from 'react'

/**
 * Tilts its children in 3D toward the pointer.
 *
 * The rotation is written straight to the node's style rather than held in React state:
 * a pointermove fires dozens of times a second, and re-rendering the subtree on each one
 * would cost far more than the effect is worth.
 *
 * Note this wraps BorderGlow, which does its own pointer math off getBoundingClientRect.
 * A rotated element reports a larger rect, so the glow's edge detection drifts slightly
 * while tilted. Both effects track the same cursor, so they still read as one motion —
 * but that is why `max` stays modest rather than going for a dramatic angle.
 */
export default function TiltCard({ children, max = 8, className = '' }) {
  const ref = useRef(null)

  const handleMove = useCallback(
    e => {
      const el = ref.current
      if (!el) return
      const { width, height, left, top } = el.getBoundingClientRect()
      // -0.5..0.5 either side of centre, so the sign flips as the pointer crosses it.
      const px = (e.clientX - left) / width - 0.5
      const py = (e.clientY - top) / height - 0.5
      // Y drives rotateX inverted: pointer above centre should tip the top edge away.
      el.style.transform = `perspective(1100px) rotateX(${(-py * max).toFixed(2)}deg) rotateY(${(px * max).toFixed(2)}deg)`
    },
    [max]
  )

  const handleLeave = useCallback(() => {
    const el = ref.current
    if (!el) return
    el.style.transform = 'perspective(1100px) rotateX(0deg) rotateY(0deg)'
  }, [])

  return (
    <div
      ref={ref}
      onPointerMove={handleMove}
      onPointerLeave={handleLeave}
      className={`transition-transform duration-200 ease-out will-change-transform ${className}`}
      style={{ transformStyle: 'preserve-3d' }}
    >
      {children}
    </div>
  )
}
