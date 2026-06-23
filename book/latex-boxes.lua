-- Render the custom case blocks as styled tcolorboxes in the PDF (LaTeX)
-- output, and the .key-term spans as colored bold. No-op for other formats.

local boxes = {
  ["case-at-a-glance"]  = { "At a Glance",        "cbaccent" },
  ["context-box"]       = { "Background",         "cbmuted"  },
  ["argument"]          = { "Argument",           "cbdark"   },
  ["objection"]         = { "Objection",          "cbaccent" },
  ["recap"]             = { "Recap",              "cbteal"   },
  ["learning-outcomes"] = { "Learning Outcomes",  "cbteal"   },
  ["thought-question"]  = { "Discuss",            "cbwarm"   },
}

function Div(el)
  if not FORMAT:match("latex") then return nil end
  for cls, spec in pairs(boxes) do
    if el.classes:includes(cls) then
      local title, color = spec[1], spec[2]
      local out = el.content:clone()
      table.insert(out, 1,
        pandoc.RawBlock("latex", "\\begin{casebox}{" .. title .. "}{" .. color .. "}"))
      table.insert(out,
        pandoc.RawBlock("latex", "\\end{casebox}"))
      return out
    end
  end
  return nil
end

function Span(el)
  if not FORMAT:match("latex") then return nil end
  if el.classes:includes("key-term") then
    local out = { pandoc.RawInline("latex", "\\textkey{") }
    for _, inline in ipairs(el.content) do out[#out + 1] = inline end
    out[#out + 1] = pandoc.RawInline("latex", "}")
    return out
  end
  return nil
end
