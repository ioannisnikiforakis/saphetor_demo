import os, sys
import argparse
import traceback
import vcfpy

MAX_COUNT = 0
MAX_BULK_LINES = 100

def insert_to_db_bulk(lines):
    global MAX_BULK_LINES
    pass

def main(argv=None):
    global MAX_COUNT

    """Main program entry point for parsing command line arguments and executing the parse/import for the VCF file"""
    parser = argparse.ArgumentParser(description="VCF Parser and importer")
    parser.add_argument("--input-vcf", type=str, required=True, help="Path to VCF file to read")
    parser.add_argument("--max-records", type=int, default=0, help="Max number of records to read from file(Optional)")
    parser.add_argument("--verbose", type=bool, default=False, help="Print line content")
    
    args = parser.parse_args(argv)
    if args.input_vcf and os.path.isfile(args.input_vcf):
        if args.max_records > 0:
            MAX_COUNT = args.max_records
        cnt=0
        try:
            # Open file, this will read in the header
            reader = vcfpy.Reader.from_path(args.input_vcf)
            # Build and print header
            header = ["#CHROM", "POS", "ID", "REF", "ALT"]
            print("\t".join(header))
            
            for record in reader:
                # if not record.is_snv():
                #    continue
                line = [record.CHROM ,record.POS, record.ID, record.REF]
                line.append([alt.value for alt in record.ALT])
                # if len(record.ALT) < 1:
                #     print(line)
                # if len(record.ALT) > 1:
                #     print([alt.value for alt in record.ALT])
                #     print(len(record.ALT))
                # if len(record.ID) > 1:
                #     print(record.ID)
                if args.verbose:
                    print("\t".join(map(str, line)))
                cnt+=1
                if MAX_COUNT and cnt >= MAX_COUNT:
                    break
        except Exception as err:
            traceback.print_exc()
        finally:
            print(f"Final count of lines processed:{cnt}")
    else:
        print(f"ERROR: File {args.input_vcf} could not be found or is not valid")

if __name__ == "__main__":
    sys.exit(main())