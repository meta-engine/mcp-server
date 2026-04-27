import { StockItem } from '../aggregates/StockItem';

/** Service providing business operations for inventory stock. */
export class StockService {
  create(input: Partial<StockItem>): StockItem {
    void input;
    throw new Error('not implemented');
  }

  findById(id: string): StockItem | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): StockItem[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: string): void {
    void id;
    throw new Error('not implemented');
  }
}
