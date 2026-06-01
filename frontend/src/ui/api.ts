export type Product = { id: number; name: string; sku: string; price: string; stock_qty: number };
export type Customer = { id: number; name: string; email: string };
export type OrderItem = { product_id: number; quantity: number; unit_price: string };
export type Order = { id: number; customer_id: number; created_at: string; status: string; items: OrderItem[] };

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail?.message || body?.detail || res.statusText);
  }
  return (await res.json()) as T;
}

export const api = {
  listProducts: () => apiFetch<Product[]>("/api/products"),
  createProduct: (p: { name: string; sku: string; price: string; stock_qty: number }) =>
    apiFetch<Product>("/api/products", { method: "POST", body: JSON.stringify(p) }),
  listCustomers: () => apiFetch<Customer[]>("/api/customers"),
  createCustomer: (c: { name: string; email: string }) =>
    apiFetch<Customer>("/api/customers", { method: "POST", body: JSON.stringify(c) }),
  listOrders: () => apiFetch<Order[]>("/api/orders"),
  createOrder: (o: { customer_id: number; items: { product_id: number; quantity: number }[] }) =>
    apiFetch<Order>("/api/orders", { method: "POST", body: JSON.stringify(o) }),
};

