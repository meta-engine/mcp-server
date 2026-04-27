import { StockItem } from "../aggregates/StockItem";

/** Repository contract for persisting StockItem aggregates. */
export class StockRepository {
  create(input: Partial<StockItem>): StockItem {
    void input;
    throw new Error("not implemented");
  }

  findById(id: string): StockItem | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): StockItem[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
