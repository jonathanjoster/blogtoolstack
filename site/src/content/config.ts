import { defineCollection, z } from 'astro:content';

const articles = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.date(),
    format: z.enum(['comparison', 'review', 'how-to', 'listicle']),
    targetKeyword: z.string(),
    leadMagnet: z.boolean().default(false),
  }),
});

export const collections = { articles };
