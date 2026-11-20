"""Reusable building blocks for step-by-step explainer videos.

camera      - spring-damped camera path (inertia, slight overshoot, handheld drift, cut detection)
post        - colour grade, vignette, depth-of-field edge blur, motion blur, whip-pan, film look
shadows     - soft projected shadows + ambient occlusion for the isometric renderer
characters  - 'Pegs' mascots v2 (arms, poses, brows, look-at, reactions)
widgets     - animated pop-ups: note, warn, check, stamp, meter, bars, count, equation, graph,
              arrow, tracker, follow card
parts       - reusable 2.5D parts: bolts, panels, button panels, LED, digital display, gear,
              pipe, fan, screen, crate
palette     - harmonised colours and helpers
See LIBRARY.md for how to use and extend it.
"""
