/**
 * rehype plugin that transforms [N] citation markers in text nodes
 * into <sup> badge elements, linked to the source URL if available.
 *
 * Operates on the parsed HTML AST — markdown links like [text](url)
 * are already element nodes at this stage, so a simple /\[(\d{1,2})\]/g
 * on text nodes is unambiguous (no lookbehind hacks needed).
 */

import { visit, SKIP } from 'unist-util-visit';
import type { Root, Element, Text, ElementContent } from 'hast';
import type { Plugin } from 'unified';
import type { Source } from './SourcesFooter';

const CITATION_RE = /\[(\d{1,2})\]/g;
const SKIP_TAGS = new Set(['code', 'pre']);

export interface RehypeCitationsOptions {
  sources: Source[];
}

function buildCitationNode(
  num: number,
  source: Source | undefined,
): ElementContent {
  const supElement: Element = {
    type: 'element',
    tagName: 'sup',
    properties: {
      className: source?.url
        ? ['citation-ref', 'citation-ref--link']
        : ['citation-ref'],
    },
    children: [{ type: 'text', value: String(num) }],
  };

  if (source?.url) {
    return {
      type: 'element',
      tagName: 'a',
      properties: {
        href: source.url,
        target: '_blank',
        rel: ['noopener', 'noreferrer'],
        title: source.title,
      },
      children: [supElement],
    };
  }

  return supElement;
}

export const rehypeCitations: Plugin<[RehypeCitationsOptions], Root> =
  ({ sources }) =>
  (tree) => {
    visit(tree, 'text', (node: Text, index, parent) => {
      if (index === undefined || index === null || !parent) return;

      // Skip text inside <code> or <pre>
      if (
        parent.type === 'element' &&
        SKIP_TAGS.has((parent as Element).tagName)
      ) {
        return;
      }

      const text = node.value;
      if (!text.includes('[')) return;

      // Reset — module-scoped /g regex retains lastIndex between calls
      CITATION_RE.lastIndex = 0;

      const segments: ElementContent[] = [];
      let lastIndex = 0;
      let match: RegExpExecArray | null;

      while ((match = CITATION_RE.exec(text)) !== null) {
        const [fullMatch, numStr] = match;
        const start = match.index;
        const num = parseInt(numStr!, 10);

        if (start > lastIndex) {
          segments.push({ type: 'text', value: text.slice(lastIndex, start) });
        }

        segments.push(buildCitationNode(num, sources.find((s) => s.index === num)));
        lastIndex = start + fullMatch.length;
      }

      if (segments.length === 0) return;

      if (lastIndex < text.length) {
        segments.push({ type: 'text', value: text.slice(lastIndex) });
      }

      (parent as Element).children.splice(index, 1, ...segments);
      return [SKIP, index + segments.length] as const;
    });
  };
