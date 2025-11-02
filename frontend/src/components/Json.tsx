export function Json({ data }: { data: unknown }) {
    return (
        <pre
            style={{
                background: "#0b0b0b",
                color: "#e6e6e6",
                padding: 12,
                borderRadius: 8,
                overflowX: "auto"
            }}
        >
            {JSON.stringify(data, null, 2)}
        </pre>
    )
}