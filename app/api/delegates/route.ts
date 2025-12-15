import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET() {
  try {
    const { data, error } = await supabase
      .from('delegates')
      .select('*');

    if (error) throw error;

    return NextResponse.json({ status: 'success', data });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch delegates' },
      { status: 500 }
    );
  }
}
