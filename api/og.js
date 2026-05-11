import { ImageResponse } from '@vercel/og';

export const config = {
  runtime: 'edge',
};

export default function handler(req) {
  try {
    return new ImageResponse(
      (
        <div
          style={{
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0E1230 0%, #1A1F3A 60%, #2D3355 100%)',
            padding: '60px',
            position: 'relative',
          }}
        >
          {/* Background watermark */}
          <div
            style={{
              position: 'absolute',
              opacity: 0.06,
              fontSize: '320px',
              fontWeight: '900',
              color: '#C5A55A',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontFamily: 'serif',
            }}
          >
            דעת
          </div>

          {/* Thin gold top line */}
          <div
            style={{
              position: 'absolute',
              top: '48px',
              left: '60px',
              right: '60px',
              height: '1px',
              background: '#C5A55A',
              opacity: 0.5,
            }}
          />

          {/* Thin gold bottom line */}
          <div
            style={{
              position: 'absolute',
              bottom: '48px',
              left: '60px',
              right: '60px',
              height: '1px',
              background: '#C5A55A',
              opacity: 0.5,
            }}
          />

          {/* Main content */}
          <div
            style={{
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0px',
              textAlign: 'center',
              zIndex: 10,
            }}
          >
            {/* Surtitre */}
            <div
              style={{
                fontSize: '22px',
                fontWeight: '400',
                color: '#C5A55A',
                letterSpacing: '6px',
                textTransform: 'uppercase',
                marginBottom: '40px',
                fontFamily: 'serif',
              }}
            >
              HILKHOT CHABBAT · EN FRANÇAIS · À TON NIVEAU
            </div>

            {/* DAAT in large Latin serif */}
            <div
              style={{
                fontSize: '140px',
                fontWeight: '700',
                color: '#FFFFFF',
                letterSpacing: '20px',
                lineHeight: '1',
                fontFamily: 'serif',
                marginBottom: '8px',
              }}
            >
              DAAT
            </div>

            {/* Hebrew דעת in gold */}
            <div
              style={{
                fontSize: '80px',
                fontWeight: '700',
                color: '#C5A55A',
                letterSpacing: '4px',
                lineHeight: '1',
                fontFamily: 'serif',
                direction: 'rtl',
                marginBottom: '48px',
              }}
            >
              דעת
            </div>

            {/* Tagline */}
            <div
              style={{
                fontSize: '28px',
                fontWeight: '300',
                color: '#EEE6D6',
                letterSpacing: '2px',
                fontFamily: 'serif',
                opacity: 0.85,
              }}
            >
              Étude de la Halakha en français
            </div>
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      },
    );
  } catch (e) {
    console.error('Error generating OG image:', e);
    return new Response('Failed to generate image', { status: 500 });
  }
}
