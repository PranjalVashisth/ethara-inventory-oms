import React, { useEffect, useMemo, useState } from "react";
import { api, Customer, Order, Product } from "./api";

function Section({
  title,
  subtitle,
  children,
  right,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  right?: React.ReactNode;
}) {
  return (
    <div className="card">
      <div className="cardHeader">
        <div>
          <div className="cardTitle">{title}</div>
          {subtitle ? <div className="cardSub">{subtitle}</div> : null}
        </div>
        {right ? <div className="cardRight">{right}</div> : null}
      </div>
      {children}
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: string; tone?: "ok" | "warn" | "info" }) {
  return (
    <div className={`stat ${tone ? `stat-${tone}` : ""}`}>
      <div className="statLabel">{label}</div>
      <div className="statValue">{value}</div>
    </div>
  );
}

function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="empty">
      <div className="emptyTitle">{title}</div>
      <div className="emptyDetail">{detail}</div>
    </div>
  );
}

export function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<null | "refresh" | "create_product" | "create_customer" | "create_order">(null);
  const [notice, setNotice] = useState<string | null>(null);

  const [pName, setPName] = useState("");
  const [pSku, setPSku] = useState("");
  const [pPrice, setPPrice] = useState("0.00");
  const [pStock, setPStock] = useState(0);

  const [cName, setCName] = useState("");
  const [cEmail, setCEmail] = useState("");

  const [oCustomerId, setOCustomerId] = useState<number | "">("");
  const [oProductId, setOProductId] = useState<number | "">("");
  const [oQty, setOQty] = useState(1);

  useEffect(() => {
    if (!notice) return;
    const t = window.setTimeout(() => setNotice(null), 2500);
    return () => window.clearTimeout(t);
  }, [notice]);

  const refresh = async () => {
    setError(null);
    setNotice(null);
    setBusy("refresh");
    const [ps, cs, os] = await Promise.all([api.listProducts(), api.listCustomers(), api.listOrders()]);
    setProducts(ps);
    setCustomers(cs);
    setOrders(os);
    setBusy(null);
  };

  useEffect(() => {
    refresh().catch((e) => setError(String(e.message || e)));
  }, []);

  const productOptions = useMemo(() => products.map((p) => ({ label: `${p.name} (${p.sku}) — stock ${p.stock_qty}`, value: p.id })), [products]);
  const customerOptions = useMemo(() => customers.map((c) => ({ label: `${c.name} (${c.email})`, value: c.id })), [customers]);
  const productsById = useMemo(() => new Map(products.map((p) => [p.id, p])), [products]);
  const customersById = useMemo(() => new Map(customers.map((c) => [c.id, c])), [customers]);
  const lowStockCount = useMemo(() => products.filter((p) => p.stock_qty <= 2).length, [products]);

  return (
    <div className="page">
      <div className="topbar">
        <div className="brand">
          <div className="brandTitle">Ethara Inventory & Order Management</div>
          <div className="brandSub">Products • Customers • Orders (stock auto-reduces)</div>
        </div>
        <div className="topbarActions">
          <button
            className="btn btn-ghost"
            onClick={() => refresh().catch((e) => setError(String(e.message || e)))}
            disabled={busy !== null}
          >
            {busy === "refresh" ? "Refreshing…" : "Refresh"}
          </button>
        </div>
      </div>

      <div className="stats">
        <Stat label="Products" value={String(products.length)} tone="info" />
        <Stat label="Customers" value={String(customers.length)} tone="info" />
        <Stat label="Orders" value={String(orders.length)} tone="info" />
        <Stat label="Low Stock (≤2)" value={String(lowStockCount)} tone={lowStockCount > 0 ? "warn" : "ok"} />
      </div>

      {error ? <div className="banner banner-error">{error}</div> : null}
      {notice ? <div className="banner banner-ok">{notice}</div> : null}

      <div className="grid">
        <Section title="Create Product" subtitle="SKUs must be unique. Stock is validated on order placement.">
          <div className="row">
            <div className="field">
              <label>Name</label>
              <input placeholder="e.g. iPhone 16" value={pName} onChange={(e) => setPName(e.target.value)} />
            </div>
            <div className="field">
              <label>SKU (unique)</label>
              <input placeholder="e.g. SKU-001" value={pSku} onChange={(e) => setPSku(e.target.value)} />
            </div>
          </div>
          <div className="row">
            <div className="field">
              <label>Price</label>
              <input placeholder="0.00" value={pPrice} onChange={(e) => setPPrice(e.target.value)} />
            </div>
            <div className="field">
              <label>Stock Qty</label>
              <input
                placeholder="0"
                type="number"
                min={0}
                value={pStock}
                onChange={(e) => setPStock(Number(e.target.value))}
              />
            </div>
          </div>
          <button
            className="btn"
            onClick={async () => {
              try {
                setError(null);
                setNotice(null);
                setBusy("create_product");
                await api.createProduct({ name: pName, sku: pSku, price: pPrice, stock_qty: pStock });
                setPName("");
                setPSku("");
                setPPrice("0.00");
                setPStock(0);
                await refresh();
                setNotice("Product created.");
              } catch (e: any) {
                setError(String(e.message || e));
              } finally {
                setBusy(null);
              }
            }}
            disabled={busy !== null || !pName.trim() || !pSku.trim()}
          >
            {busy === "create_product" ? "Creating…" : "Create"}
          </button>
        </Section>

        <Section title="Create Customer" subtitle="Emails must be unique.">
          <div className="row">
            <div className="field">
              <label>Name</label>
              <input placeholder="e.g. Alice" value={cName} onChange={(e) => setCName(e.target.value)} />
            </div>
            <div className="field">
              <label>Email (unique)</label>
              <input placeholder="alice@example.com" value={cEmail} onChange={(e) => setCEmail(e.target.value)} />
            </div>
          </div>
          <button
            className="btn"
            onClick={async () => {
              try {
                setError(null);
                setNotice(null);
                setBusy("create_customer");
                await api.createCustomer({ name: cName, email: cEmail });
                setCName("");
                setCEmail("");
                await refresh();
                setNotice("Customer created.");
              } catch (e: any) {
                setError(String(e.message || e));
              } finally {
                setBusy(null);
              }
            }}
            disabled={busy !== null || !cName.trim() || !cEmail.trim()}
          >
            {busy === "create_customer" ? "Creating…" : "Create"}
          </button>
        </Section>

        <Section
          title="Create Order"
          subtitle="Orders fail if stock is insufficient; stock reduces automatically."
          right={
            <div className="chip">
              {products.length === 0 ? "Add a product first" : customers.length === 0 ? "Add a customer first" : "Ready"}
            </div>
          }
        >
          <div className="row">
            <div className="field">
              <label>Customer</label>
              <select value={oCustomerId} onChange={(e) => setOCustomerId(e.target.value ? Number(e.target.value) : "")}>
                <option value="">Select Customer</option>
                {customerOptions.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Product</label>
              <select value={oProductId} onChange={(e) => setOProductId(e.target.value ? Number(e.target.value) : "")}>
                <option value="">Select Product</option>
                {productOptions.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="row">
            <div className="field field-small">
              <label>Qty</label>
              <input type="number" min={1} value={oQty} onChange={(e) => setOQty(Number(e.target.value))} />
            </div>
          </div>
          <button
            className="btn"
            disabled={oCustomerId === "" || oProductId === "" || oQty <= 0}
            onClick={async () => {
              try {
                setError(null);
                setNotice(null);
                setBusy("create_order");
                await api.createOrder({
                  customer_id: Number(oCustomerId),
                  items: [{ product_id: Number(oProductId), quantity: oQty }],
                });
                setOQty(1);
                await refresh();
                setNotice("Order placed. Stock updated.");
              } catch (e: any) {
                setError(String(e.message || e));
              } finally {
                setBusy(null);
              }
            }}
          >
            {busy === "create_order" ? "Placing…" : "Place Order"}
          </button>
        </Section>

        <Section title="Products" subtitle="Inventory is reduced automatically when orders are placed.">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>SKU</th>
                <th>Price</th>
                <th>Stock</th>
              </tr>
            </thead>
            <tbody>
              {products.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <EmptyState title="No products yet" detail="Create a product to start tracking inventory." />
                  </td>
                </tr>
              ) : (
                products.map((p) => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td>
                      <div className="cellMain">{p.name}</div>
                      <div className="cellSub">SKU: {p.sku}</div>
                    </td>
                    <td>
                      <span className="badge badge-neutral">{p.sku}</span>
                    </td>
                    <td>{p.price}</td>
                    <td>
                      <span className={`badge ${p.stock_qty === 0 ? "badge-bad" : p.stock_qty <= 2 ? "badge-warn" : "badge-ok"}`}>
                        {p.stock_qty}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </Section>

        <Section title="Customers" subtitle="Emails must be unique.">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
              </tr>
            </thead>
            <tbody>
              {customers.length === 0 ? (
                <tr>
                  <td colSpan={3}>
                    <EmptyState title="No customers yet" detail="Create a customer before placing an order." />
                  </td>
                </tr>
              ) : (
                customers.map((c) => (
                  <tr key={c.id}>
                    <td>{c.id}</td>
                    <td className="cellMain">{c.name}</td>
                    <td>{c.email}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </Section>

        <Section title="Orders" subtitle="Latest orders appear first.">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Customer</th>
                <th>Status</th>
                <th>Created</th>
                <th>Items</th>
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <EmptyState title="No orders yet" detail="Place an order to see it here and auto-reduce stock." />
                  </td>
                </tr>
              ) : (
                orders.map((o) => (
                  <tr key={o.id}>
                    <td>{o.id}</td>
                    <td>
                      <div className="cellMain">{customersById.get(o.customer_id)?.name ?? `Customer #${o.customer_id}`}</div>
                      <div className="cellSub">{customersById.get(o.customer_id)?.email ?? ""}</div>
                    </td>
                    <td>
                      <span className="badge badge-neutral">{o.status}</span>
                    </td>
                    <td>{new Date(o.created_at).toLocaleString()}</td>
                    <td>
                      {o.items.map((it, idx) => {
                        const p = productsById.get(it.product_id);
                        const label = p ? `${p.name} (${p.sku})` : `Product #${it.product_id}`;
                        return (
                          <span key={idx} className="pill">
                            {label} × {it.quantity}
                          </span>
                        );
                      })}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </Section>
      </div>
    </div>
  );
}
