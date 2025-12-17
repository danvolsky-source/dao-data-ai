import { NextResponse } from 'next/server';

// Proxy to FastAPI backend instead of direct Supabase access
export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    
    // If no API URL is configured, return empty data instead of failing
    if (!apiUrl) {
      return NextResponse.json({ status: 'success', data: [] });
    }
    
    const response = await fetch(`${apiUrl}/api/votes`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`FastAPI returned ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json({ status: 'success', data });
  } catch (error) {
    console.error('Error proxying to FastAPI:', error);
    return NextResponse.json(
      { status: 'success', data: [] },
      { status: 200 }
    );
  }
}
