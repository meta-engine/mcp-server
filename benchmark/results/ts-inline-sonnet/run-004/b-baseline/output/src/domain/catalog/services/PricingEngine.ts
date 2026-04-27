import { Product } from "../aggregates/Product";

/** Engine for computing and applying product pricing rules. */
export class PricingEngine {
  create(input: Partial<Product>): Product {
    void input;
    throw new Error("not implemented");
  }

  findById(id: string): Product | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): Product[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
