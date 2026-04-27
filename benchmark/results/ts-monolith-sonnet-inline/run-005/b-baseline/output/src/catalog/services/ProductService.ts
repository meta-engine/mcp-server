import { Id } from '../../shared/value-objects/Id';
import { Product } from '../aggregates/Product';

/** Manages product lifecycle in the catalog. */
export class ProductService {
  create(input: Partial<Product>): Product { throw new Error('not implemented'); }
  findById(id: Id): Product | null { throw new Error('not implemented'); }
  list(limit: number): Product[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
