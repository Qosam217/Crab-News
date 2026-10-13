
"use client";

import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

type TrendData2 = {
    date: string;
    articles: number;
    words: number;
};

type TrendChartProps2 = {
    data: TrendData2[];
};

export function TrendChart2({ data }: TrendChartProps2) {
    return (
        <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart
                    data={data}
                    margin={{
                        top: 10,
                        right: 12,
                        left: 12,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#334155"
                    />

                    <XAxis
                        dataKey="date"
                        stroke="#94a3b8"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) =>
                            new Date(`${value}T00:00:00`).toLocaleDateString(
                                "id-ID",
                                { day: "2-digit", month: "short" }
                            )
                        }
                    />

                    {/* Sumbu Y kiri: volume kata */}
                    <YAxis
                        yAxisId="words"
                        orientation="left"
                        stroke="#38bdf8"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) =>
                            Number(value).toLocaleString("id-ID")
                        }
                    />

                    {/* Sumbu Y kanan: jumlah artikel */}
                    <YAxis
                        yAxisId="articles"
                        orientation="right"
                        stroke="#a78bfa"
                        tick={{ fontSize: 12 }}
                        allowDecimals={false}
                    />

                    <Tooltip
                        labelFormatter={(label) =>
                            new Date(`${label}T00:00:00`).toLocaleDateString(
                                "id-ID",
                                {
                                    day: "numeric",
                                    month: "long",
                                    year: "numeric",
                                }
                            )
                        }
                        formatter={(value, name) => [
                            Number(value).toLocaleString("id-ID"),
                            name === "words"
                                ? "Frekuensi Kata"
                                : "Jumlah Artikel",
                        ]}
                        contentStyle={{
                            backgroundColor: "#0f172a",
                            border: "1px solid #334155",
                            borderRadius: "8px",
                            color: "#f8fafc",
                        }}
                    />

                    <Line
                        yAxisId="words"
                        type="monotone"
                        dataKey="words"
                        name="words"
                        stroke="#38bdf8"
                        strokeWidth={2.5}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                    />

                    <Line
                        yAxisId="articles"
                        type="monotone"
                        dataKey="articles"
                        name="articles"
                        stroke="#a78bfa"
                        strokeWidth={2.5}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
