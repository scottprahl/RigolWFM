//from http://nsweb.tn.tudelft.nl/~gsteele/rigol2dat/rigol2dat.C
//tested with a Rigol DS1022C datafiles
//
// Compile with, for example:
//
// Linux:
//
// g++ -Wall -g -o rigol2dat rigol2dat.C
//
// Mingw cross compile:
//
// i586-mingw32msvc-g++ rigol2dat.C -o rigol2dat.exe

#include <stdio.h>

#include <stdint.h>

#include <string.h>

#include <string>

using namespace std;

#
define MAX_PTS 524288 * 2

int main(int argc, char ** argv) {
    uint32_t npts;
    uint64_t time_scale;
    int64_t time_delay;
    uint8_t ch1rec;
    uint8_t ch2rec;

    uint32_t ch1sc;
    int16_t ch1pos;
    uint32_t ch2sc;
    int16_t ch2pos;

    uint8_t data[MAX_PTS]; // biggest size from our rigol

    int nread;

    // Stuff in real units

    double trace_length_sec;
    double ch1sc_v;
    double ch1pos_v;
    double ch2sc_v;
    double ch2pos_v;

    char filename[1024];
    strncpy(filename, argv[1], 1024);
    char basename[1024];
    strcpy(basename, filename);
    char * p = strchr(basename, '.');
    * p = 0;
    string outname;

    FILE * fp = fopen(argv[1], "r");
    FILE * out;

    fseek(fp, 28, SEEK_SET);  // skip 28,
    fread( & npts, sizeof(npts), 1, fp);  //28+4=32
    fprintf(stderr, "npts: %d\n", npts);
    if (npts > MAX_PTS) {
        fprintf(stderr, "Too many points: %d > %d!\n", npts, MAX_PTS);
        exit(-1);
    }

    fseek(fp, 36, SEEK_SET);  // skip 4, 36+4=40
    fread( & ch1sc, sizeof(ch1sc), 1, fp);
    fprintf(stderr, "ch1sc: %d\n", ch1sc);

    fseek(fp, 40, SEEK_SET);  // skip 0, 40+4=44
    fread( & ch1pos, sizeof(ch1pos), 1, fp);
    fprintf(stderr, "ch1pos: %d\n", ch1pos);

    fseek(fp, 49, SEEK_SET); // skip 5, 49+1=50
    fread( & ch1rec, sizeof(ch1rec), 1, fp);
    fprintf(stderr, "ch1rec: %d\n", ch1rec);

    fseek(fp, 60, SEEK_SET); // skip 10, 60+4=64
    fread( & ch2sc, sizeof(ch2sc), 1, fp);
    fprintf(stderr, "ch2sc: %d\n", ch2sc);

    fseek(fp, 64, SEEK_SET); // skip 0, 64+4 = 68
    fread( & ch2pos, sizeof(ch2pos), 1, fp);
    fprintf(stderr, "ch2pos: %d\n", ch2pos);
    
    fseek(fp, 73, SEEK_SET); // skip 5, 73+1=74
    fread( & ch2rec, sizeof(ch2rec), 1, fp);
    fprintf(stderr, "ch2rec: %d\n", ch2rec);

    fseek(fp, 84, SEEK_SET); // skip 10, 84+8
    fread( & time_scale, sizeof(time_scale), 1, fp);
    fprintf(stderr, "time_scale: %lld ps = %e s\n", time_scale, 1.0 * time_scale / 1e12);

    // The next int64
    //fseek(fp, 84, SEEK_SET); // skip 0, 92+8=100
    fread( & time_delay, sizeof(time_delay), 1, fp);
    fprintf(stderr, "time_delay: %lld ps = %e s\n", time_delay, 1.0 * time_scale / 1e12);

    // Now get things in real units

    ch1sc_v = 1e-6 * ch1sc;
    ch1pos_v = 1.0 * ch1pos * ch1sc_v;

    ch2sc_v = 1e-6 * ch2sc;
    ch2pos_v = 1.0 * ch2pos * ch2sc_v;

    trace_length_sec = 1.0 * time_scale / 1e12 * 12;

    fprintf(stderr, "\nReal units:\n\n"
        "ch1sc_v: %e\n"
        "ch1pos_v: %e\n"
        "ch2sc_v: %e\n"
        "ch2pos_v: %e\n"
        "trace_sec: %e\n",
        ch1sc_v, ch1pos_v,
        ch2sc_v, ch2pos_v,
        trace_length_sec);

    if (ch1rec) {
        outname = basename;
        outname += ".1.dat";
        out = fopen(outname.c_str(), "w");

        fseek(fp, 272, SEEK_SET);   // 100+172=272, read npts bytes
        nread = fread(data, sizeof(data[0]), npts, fp);
        if (nread != npts) {
            fprintf(stderr, "Short read: nread %d is not same as npts %d", nread, npts);
            exit(-1);
        }

        for (int i = 0; i < npts; i++)
            fprintf(out, "%e %e\n",
                trace_length_sec * i / (npts - 1),
                ch1sc_v * (100.0 - data[i] + 1) / 25.0 - ch1pos_v);

        fclose(out);
    }

    if (ch2rec) {
        outname = basename;
        outname += ".2.dat";
        out = fopen(outname.c_str(), "w");

        fseek(fp, 272 + npts, SEEK_SET);  // read npts bytes again
        nread = fread(data, sizeof(data[0]), npts, fp);
        if (nread != npts) {
            fprintf(stderr, "Short read: nread %d is not same as npts %d", nread, npts);
            exit(-1);
        }

        for (int i = 0; i < npts; i++)
            fprintf(out, "%e %e\n",
                trace_length_sec * i / (npts - 1),
                ch2sc_v * (100.0 - data[i]) / 25.0 - ch2pos_v);

        fclose(out);
    }

    fclose(fp);
}