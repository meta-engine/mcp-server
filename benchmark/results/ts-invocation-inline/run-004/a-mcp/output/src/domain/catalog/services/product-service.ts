import { Product } from '../aggregates/product';

/** ProductService service. */
export class ProductService {

  create(input: Partial<Product>): Product { throw new Error('not implemented'); }

  findById(id: string): Product | null { throw new Error('not implemented'); }

  list(limit: number): Product[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
