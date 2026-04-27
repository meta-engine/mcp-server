import { Product } from '../aggregates/product';
import { Id } from '../../shared/value-objects/id';

/** ProductService service. */
export class ProductService {

  create(input: Partial<Product>): Product { throw new Error('not implemented'); }

  findById(id: Id): Product | null { throw new Error('not implemented'); }

  list(limit: number): Product[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
