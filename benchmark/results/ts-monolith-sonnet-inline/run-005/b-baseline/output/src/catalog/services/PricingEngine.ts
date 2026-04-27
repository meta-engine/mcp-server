import { Id } from '../../shared/value-objects/Id';
import { Product } from '../aggregates/Product';

/** Computes and manages pricing for catalog products. */
export class PricingEngine {
  create(input: Partial<Product>): Product { throw new Error('not implemented'); }
  findById(id: Id): Product | null { throw new Error('not implemented'); }
  list(limit: number): Product[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
