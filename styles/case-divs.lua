-- Map Quarto custom divs/spans to Word paragraph & character styles.
-- The matching styles must exist (or will be auto-created) in
-- styles/case-reference.docx. Edit them in Word to restyle globally.

local div_styles = {
  ["case-at-a-glance"] = "CaseGlance",
  ["context-box"]      = "ContextBox",
  ["callout-note"]     = "CalloutNote",
  ["pullquote"]        = "PullQuote",
}

local span_styles = {
  ["key-term"] = "KeyTerm",
}

function Div(el)
  for cls, style in pairs(div_styles) do
    if el.classes:includes(cls) then
      el.attributes["custom-style"] = style
      return el
    end
  end
end

function Span(el)
  for cls, style in pairs(span_styles) do
    if el.classes:includes(cls) then
      el.attributes["custom-style"] = style
      return el
    end
  end
end
