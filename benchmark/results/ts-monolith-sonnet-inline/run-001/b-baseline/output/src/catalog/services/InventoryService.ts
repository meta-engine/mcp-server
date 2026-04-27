import { Id } from '../../shared/value-objects/Id';
import { Product } from '../aggregates/Product';

/** Manages product inventory. */
export class InventoryService {
  create(input: Partial<Product>): Product {
    void input;
    throw new Error('not implemented');
  }

  findById(id: Id): Product | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Product[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: Id): void {
    void id;
    throw new Error('not implemented');
  }
}
