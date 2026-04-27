import { Product } from '../aggregates/Product';

/** Service providing business operations for catalog products. */
export class ProductService {
  create(input: Partial<Product>): Product {
    void input;
    throw new Error('not implemented');
  }

  findById(id: string): Product | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Product[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: string): void {
    void id;
    throw new Error('not implemented');
  }
}
