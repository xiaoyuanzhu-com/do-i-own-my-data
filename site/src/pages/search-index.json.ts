import type { APIRoute } from 'astro';
import { loadProducts } from '../data/products';

export const GET: APIRoute = () => {
  const products = loadProducts();
  const index = products.map(p => ({
    slug: p.slug,
    name: p.name,
    vendor: p.vendor,
    tags: p.tags,
    description: p.description,
  }));
  return new Response(JSON.stringify(index), {
    headers: { 'Content-Type': 'application/json' },
  });
};
