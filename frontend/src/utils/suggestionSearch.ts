export interface SuggestionItem {
    id: string | number;
    name: string;
    type: 'person' | 'place' | 'event';
    slug: string;
    description?: string;
}

type TrieNode = {
    children: Map<string, TrieNode>;
    items: SuggestionItem[];
    itemKeys: Set<string>;
};

const createNode = (): TrieNode => ({
    children: new Map(),
    items: [],
    itemKeys: new Set()
});

export class SuggestionIndex {
    private suggestions: SuggestionItem[];
    private rootAll: TrieNode;
    private rootByType: Record<'person' | 'place' | 'event', TrieNode>;
    private slugIndex: Map<string, SuggestionItem>;

    constructor(suggestions: SuggestionItem[]) {
        this.suggestions = suggestions;
        this.rootAll = createNode();
        this.rootByType = {
            person: createNode(),
            place: createNode(),
            event: createNode()
        };
        this.slugIndex = new Map();
        this.buildIndex();
    }

    private buildIndex(): void {
        for (const item of this.suggestions) {
            // O(1) slug resolution
            const slugKey = `${item.type}:${item.slug}`;
            this.slugIndex.set(slugKey, item);

            // Insert both name and slug into tries so users can type either
            this.insertWord(this.rootAll, item.name, item);
            this.insertWord(this.rootAll, item.slug, item);

            const typeRoot = this.rootByType[item.type];
            this.insertWord(typeRoot, item.name, item);
            this.insertWord(typeRoot, item.slug, item);
        }
    }

    private insertWord(root: TrieNode, word: string, item: SuggestionItem): void {
        let node = root;
        const lower = word.toLowerCase();

        for (const char of lower) {
            if (!node.children.has(char)) {
                node.children.set(char, createNode());
            }
            node = node.children.get(char)!;

            // Deduplicate items per node (id is unique key)
            const key = String(item.id);
            if (!node.itemKeys.has(key)) {
                node.itemKeys.add(key);
                node.items.push(item);
            }
        }
    }

    /**
     * Prefix search via trie. If prefix is empty, returns all of the requested type.
     */
    searchPrefix(prefix: string, type?: 'person' | 'place' | 'event'): SuggestionItem[] {
        const normalized = prefix.toLowerCase();
        const root = type ? this.rootByType[type] : this.rootAll;

        if (!normalized) {
            return type ? this.getAllByType(type) : this.suggestions;
        }

        let node: TrieNode | undefined = root;
        for (const char of normalized) {
            node = node.children.get(char);
            if (!node) return [];
        }
        return node.items;
    }

    /**
     * Exact slug resolution (O(1))
     */
    searchBySlug(slug: string, type: string): SuggestionItem | undefined {
        const key = `${type}:${slug}`;
        return this.slugIndex.get(key);
    }

    /**
     * Combined search that prefers exact slug, then trie prefix results with light ranking.
     */
    search(query: string, type?: 'person' | 'place' | 'event'): SuggestionItem[] {
        const exactMatch = type ? this.searchBySlug(query, type) : undefined;
        if (exactMatch) return [exactMatch];

        const results = this.searchPrefix(query, type);
        const q = query.toLowerCase();

        // Stable-ish ordering: exact name, startsWith, then rest
        return results.slice().sort((a, b) => {
            const aName = a.name.toLowerCase();
            const bName = b.name.toLowerCase();

            if (aName === q && bName !== q) return -1;
            if (bName === q && aName !== q) return 1;

            const aStarts = aName.startsWith(q);
            const bStarts = bName.startsWith(q);
            if (aStarts && !bStarts) return -1;
            if (!aStarts && bStarts) return 1;
            return 0;
        });
    }

    getAllByType(type: 'person' | 'place' | 'event'): SuggestionItem[] {
        return this.suggestions.filter(item => item.type === type);
    }
}