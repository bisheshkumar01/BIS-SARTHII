/**
 * Join conditional class names.
 *
 * Components copied from shadcn-style registries (21st.dev, Watermelon) import `cn` from
 * `@/lib/utils`, which is clsx + tailwind-merge. We don't need the merge half: this project
 * writes its own class strings rather than accepting arbitrary overrides from callers, so a
 * plain join keeps the same call signature without two extra dependencies.
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ')
}
